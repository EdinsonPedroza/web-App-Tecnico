import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Video, ExternalLink, Calendar } from 'lucide-react';
import api from '@/lib/api';

export default function StudentVideos() {
  const { user } = useAuth();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const cRes = await api.get(`/courses?student_id=${user.id}`);
      const allVideos = [];
      for (const course of cRes.data) {
        const vRes = await api.get(`/class-videos?course_id=${course.id}`);
        allVideos.push(...vRes.data.map(v => ({ ...v, courseName: course.name })));
      }
      setVideos(allVideos);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getEmbedUrl = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&?/]+)/);
    return match ? `https://img.youtube.com/vi/${match[1]}/mqdefault.jpg` : null;
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold font-heading">Videos de Clase</h1>
          <p className="text-muted-foreground mt-1">Material audiovisual de tus cursos</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : videos.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <Video className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay videos disponibles</p>
          </CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((vid) => {
              const thumb = getEmbedUrl(vid.url);
              return (
                <Card key={vid.id} className="shadow-card hover:shadow-card-hover transition-shadow overflow-hidden flex flex-col">
                  {thumb && (
                    <div className="aspect-video bg-muted overflow-hidden">
                      <img src={thumb} alt={vid.title} className="w-full h-full object-cover" />
                    </div>
                  )}
                  <CardContent className="p-4 flex-1 flex flex-col">
                    <h3 className="text-sm font-semibold mb-1">{vid.title}</h3>
                    <Badge variant="secondary" className="w-fit text-xs mb-2">{vid.courseName}</Badge>
                    <p className="text-xs text-muted-foreground mb-3 flex-1">{vid.description}</p>
                    <div className="flex items-center justify-between mt-auto">
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(vid.created_at)}
                      </span>
                      <Button variant="outline" size="sm" asChild>
                        <a href={vid.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-3 w-3" /> Ver Video
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

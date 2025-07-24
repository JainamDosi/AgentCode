import { useQuery, useQueryClient } from '@tanstack/react-query';
import FileNode from './FileNode.jsx';
import { useEffect } from 'react';

export default function FileExplorer({ onFileOpen, refreshKey }) {
  const queryClient = useQueryClient();

  console.log("refreshKey", refreshKey);  

  // Fetch the root directory
  const { data: tree, isLoading, error, refetch } = useQuery({
    queryKey: ['fileTree'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/fs/list?path=.');
      console.log("INside call",refreshKey);
      const data = await res.json();
      console.log("data",data);
      return [{
        name: '.', // display name
        fullPath: '.', // full path for API
        type: 'folder',
        isOpen: true,
        children: data.map(child => ({
          ...child,
          fullPath: './' + child.name,
        }))
      }];
    },
    cacheTime: 0,
    staleTime: 0,
  });

  // Helper to fetch children for a folder
  function fetchChildren(path, cb) {
    fetch(`http://localhost:8000/fs/list?path=${encodeURIComponent(path)}`)
      .then(res => res.json())
      .then(cb);
  }

  // Refresh when refreshKey changes
  useEffect(() => {
    if (refreshKey !== undefined) {
      refetch();
      console.log("refetching");
    }
  }, [refreshKey, refetch]);

  // Pass this to FileNode so it can trigger a refresh after mutations
  function refreshTree() {
    refetch();
  }

  if (isLoading) return <div style={{ padding: 10 }}>Loading...</div>;
  if (error) return <div style={{ padding: 10, color: 'red' }}>Error loading files</div>;

  return (
    <div style={{ padding: 10 }}>
      {(tree || []).map((node, idx) => (
        <FileNode
        key={node.fullPath}
        idx={idx}
          node={node}
          fetchChildren={fetchChildren}
          onFileOpen={(path, name) => onFileOpen(path, name)}
          refreshTree={refreshTree}
        />
      ))}
    </div>
  );
}

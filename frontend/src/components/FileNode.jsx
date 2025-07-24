import { useState,useEffect  } from 'react';

export default function FileNode({ node, fetchChildren, onFileOpen }) {
  const [isOpen, setIsOpen] = useState(node.isOpen || false);
  const [children, setChildren] = useState(node.children || []);
  const [loaded, setLoaded] = useState(!!node.children);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showActions, setShowActions] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName] = useState(node.name);

  const buttonStyle = {
    padding: '4px 8px',
    border: '1px solid #aaa',
    borderRadius: '5px',
    background: '#000000',
    cursor: 'pointer',
    fontSize: '12px',
    transition: 'background 0.2s ease',
  };

  useEffect(() => {
    setChildren(node.children || []);
  }, [node.children]);

  const handleToggle = () => {
    if (node.type === 'folder') {
      if (!isOpen && !loaded) {
        setLoading(true);
        fetchChildren(node.fullPath, (data) => {
          setChildren(data);
          setLoaded(true);
          setIsOpen(true);
          setLoading(false);
        });
      } else {
        setIsOpen(!isOpen);
      }
    }
  };

  const handleCreate = (type) => {
    const name = prompt(`Enter ${type} name:`);
    if (!name) return;
    setLoading(true);
    fetch(`http://localhost:8000/fs/create_${type}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: node.fullPath + '/' + name }),
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to create');
        return res.json();
      })
      .then(() => {
        setLoaded(false);
        handleToggle(); // reload children
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  const handleDelete = () => {
    if (!window.confirm(`Delete ${node.name}?`)) return;
    setLoading(true);
    fetch('http://localhost:8000/fs/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: node.fullPath }),
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to delete');
        return res.json();
      })
      .then(() => window.location.reload()) // simplest: reload tree
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  const handleRename = () => {
    const basePath = node.fullPath.substring(0, node.fullPath.lastIndexOf('/'));
    const newName = prompt('Enter new name:', node.name);
    if (!newName || newName === node.name) return;
    const newPath = basePath ? `${basePath}/${newName}` : newName;
    setLoading(true);
    fetch('http://localhost:8000/fs/rename', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_path: node.fullPath, new_path: newPath }),
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to rename');
        return res.json();
      })
      .then(() => window.location.reload())
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  const handleClick = () => {
    if (node.type === 'folder') {
      handleToggle();
    } else if (node.type === 'file') {
      onFileOpen && onFileOpen(node.fullPath, node.name);
    }
  };

  return (
    <div style={{ marginLeft: 20, position: 'relative' }}>
      <div
        style={{
          cursor: node.type === 'folder' ? 'pointer' : 'default',
          display: 'inline-block',
        }}
        onClick={handleClick}
        onContextMenu={e => {
          e.preventDefault();
          setShowActions(true);
        }}
      >
        {node.type === 'folder' ? (isOpen ? '📂' : '📁') : '📄'} {node.name}
      </div>

      {showActions && (
        <span
          style={{
            marginLeft: 8,
            display: 'inline-flex',
            gap: '6px',
            padding: '6px 10px',
            background: '#f9f9f9',
            border: '1px solid #ccc',
            borderRadius: '8px',
            boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
            marginTop: '4px',
          }}
        >
          {node.type === 'folder' && (
            <>
              <button style={buttonStyle} onClick={() => handleCreate('folder')}>+Folder</button>
              <button style={buttonStyle} onClick={() => handleCreate('file')}>+File</button>
            </>
          )}
          <button style={buttonStyle} onClick={handleRename}>Rename</button>
          <button style={buttonStyle} onClick={handleDelete}>Delete</button>
          <button style={buttonStyle} onClick={() => setShowActions(false)}>Close</button>
        </span>
      )}

      {loading && <span style={{ color: 'blue' }}> Loading...</span>}
      {error && <span style={{ color: 'red' }}> {error}</span>}

      {isOpen && node.type === 'folder' && (
        <div>
          {children.map((child, idx) => (
            <FileNode
              key={child.fullPath}
              node={{
                ...child,
                fullPath: node.fullPath === '.' ? child.name : node.fullPath + '/' + child.name,
              }}
              fetchChildren={fetchChildren}
              onFileOpen={onFileOpen}
            />
          ))}
        </div>
      )}
    </div>
  );
}

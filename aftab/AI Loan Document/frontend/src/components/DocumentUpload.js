import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Button,
  Container,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Alert,
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Delete,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import axios from 'axios';

const DocumentUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadStatus, setUploadStatus] = useState({});
  const [error, setError] = useState(null);

  const onDrop = (acceptedFiles) => {
    // Filter for PDF files
    const pdfFiles = acceptedFiles.filter(
      file => file.type === 'application/pdf'
    );
    
    if (pdfFiles.length !== acceptedFiles.length) {
      setError('Only PDF files are allowed');
    }
    
    setFiles(prevFiles => [...prevFiles, ...pdfFiles]);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  const removeFile = (fileToRemove) => {
    setFiles(files.filter(file => file !== fileToRemove));
  };

  const uploadFiles = async () => {
    setUploading(true);
    setError(null);

    const token = localStorage.getItem('token');
    
    for (const file of files) {
      setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));
      setUploadStatus(prev => ({ ...prev, [file.name]: 'uploading' }));

      const formData = new FormData();
      formData.append('files', file);

      try {
        await axios.post('/api/v1/documents/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          }
        });

        setUploadStatus(prev => ({ ...prev, [file.name]: 'success' }));
      } catch (error) {
        console.error('Upload error:', error);
        setUploadStatus(prev => ({ ...prev, [file.name]: 'error' }));
        setError(error.response?.data?.detail || 'Upload failed');
      }
    }

    setUploading(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Upload Loan Documents
      </Typography>
      
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer'
        }}
      >
        <input {...getInputProps()} />
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2
          }}
        >
          <CloudUpload sx={{ fontSize: 48, color: 'primary.main' }} />
          <Typography variant="h6" align="center">
            {isDragActive
              ? 'Drop the files here'
              : 'Drag and drop PDF files here, or click to select files'}
          </Typography>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {files.length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Selected Files
          </Typography>
          <List>
            {files.map((file, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <IconButton
                    edge="end"
                    onClick={() => removeFile(file)}
                    disabled={uploading}
                  >
                    <Delete />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  {uploadStatus[file.name] === 'success' ? (
                    <CheckCircle color="success" />
                  ) : uploadStatus[file.name] === 'error' ? (
                    <Error color="error" />
                  ) : (
                    <InsertDriveFile />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={
                    uploadProgress[file.name] ? (
                      <LinearProgress
                        variant="determinate"
                        value={uploadProgress[file.name]}
                        sx={{ mt: 1 }}
                      />
                    ) : null
                  }
                />
              </ListItem>
            ))}
          </List>
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={uploadFiles}
              disabled={uploading || files.length === 0}
              startIcon={<CloudUpload />}
            >
              {uploading ? 'Uploading...' : 'Upload Files'}
            </Button>
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default DocumentUpload; 
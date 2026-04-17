import { useEffect, useRef } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useDocumentsStore } from '../store/documentsStore.js';

interface Props {
  open: boolean;
  onClose(): void;
}

export function DocumentsModal({ open, onClose }: Props) {
  const { documents, isLoading, load, upload, remove } = useDocumentsStore();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) load();
  }, [open, load]);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await upload(file);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Stack direction="row" sx={{ alignItems: 'center' }}>
          <Typography variant="h6" flex={1}>Documents</Typography>
          <IconButton size="small" onClick={onClose}><CloseIcon fontSize="small" /></IconButton>
        </Stack>
      </DialogTitle>
      <DialogContent>
        {/* Drop zone / upload */}
        <Paper
          variant="outlined"
          sx={{
            p: 3,
            mb: 2,
            textAlign: 'center',
            borderStyle: 'dashed',
            cursor: 'pointer',
            '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(74,158,255,0.04)' },
          }}
          onClick={() => inputRef.current?.click()}
        >
          <UploadFileIcon sx={{ fontSize: 32, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body2" color="text.secondary">
            Click to upload a PDF document
          </Typography>
          <input ref={inputRef} type="file" accept=".pdf" hidden onChange={handleFile} />
        </Paper>

        {/* Table */}
        {isLoading ? (
          <Box textAlign="center" py={3}><CircularProgress size={24} /></Box>
        ) : documents.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
            No documents ingested yet.
          </Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell align="right">Pages</TableCell>
                <TableCell align="right">Chunks</TableCell>
                <TableCell align="center">Status</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map(doc => (
                <TableRow key={doc.id}>
                  <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {doc.name}
                  </TableCell>
                  <TableCell align="right">{doc.pages}</TableCell>
                  <TableCell align="right">{doc.chunks}</TableCell>
                  <TableCell align="center">
                    <Typography variant="caption" sx={{ color: doc.status === 'ready' ? '#a8ff6b' : 'text.secondary' }}>
                      {doc.status}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Delete">
                      <IconButton size="small" onClick={() => remove(doc.id)}>
                        <DeleteOutlinedIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        <Box mt={2} textAlign="right">
          <Button onClick={onClose}>Close</Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}

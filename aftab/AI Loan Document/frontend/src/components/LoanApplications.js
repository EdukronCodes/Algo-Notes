import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Chip,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Visibility,
  CloudDownload,
  CheckCircle,
  Error,
  Pending,
} from '@mui/icons-material';
import axios from 'axios';

const LoanApplications = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/documents/loan-applications', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApplications(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch loan applications');
      console.error('Error fetching applications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleViewDetails = (application) => {
    setSelectedApplication(application);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
  };

  const getStatusChip = (status) => {
    const statusProps = {
      pending: { color: 'warning', icon: <Pending /> },
      approved: { color: 'success', icon: <CheckCircle /> },
      rejected: { color: 'error', icon: <Error /> },
    }[status.toLowerCase()];

    return (
      <Chip
        label={status}
        color={statusProps.color}
        icon={statusProps.icon}
        size="small"
      />
    );
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Loan Applications
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Borrower</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Interest Rate</TableCell>
              <TableCell>Tenure (Months)</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {applications
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((application) => (
                <TableRow key={application.id}>
                  <TableCell>{application.id}</TableCell>
                  <TableCell>{application.borrower_name}</TableCell>
                  <TableCell>
                    {formatCurrency(application.loan_amount)}
                  </TableCell>
                  <TableCell>{application.interest_rate}%</TableCell>
                  <TableCell>{application.tenure_months}</TableCell>
                  <TableCell>
                    {getStatusChip(application.status)}
                  </TableCell>
                  <TableCell>
                    <Button
                      startIcon={<Visibility />}
                      size="small"
                      onClick={() => handleViewDetails(application)}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={applications.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Loan Application Details
        </DialogTitle>
        <DialogContent dividers>
          {selectedApplication && (
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Application Information
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography><strong>Borrower:</strong> {selectedApplication.borrower_name}</Typography>
                <Typography><strong>Amount:</strong> {formatCurrency(selectedApplication.loan_amount)}</Typography>
                <Typography><strong>Interest Rate:</strong> {selectedApplication.interest_rate}%</Typography>
                <Typography><strong>Tenure:</strong> {selectedApplication.tenure_months} months</Typography>
                <Typography><strong>Status:</strong> {selectedApplication.status}</Typography>
                <Typography><strong>Purpose:</strong> {selectedApplication.loan_purpose}</Typography>
              </Box>

              <Typography variant="h6" gutterBottom>
                Documents
              </Typography>
              {selectedApplication.documents?.map((doc, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    mb: 1,
                    p: 1,
                    bgcolor: 'background.default',
                    borderRadius: 1
                  }}
                >
                  <Typography>{doc.filename}</Typography>
                  <Button
                    startIcon={<CloudDownload />}
                    size="small"
                    onClick={() => window.open(doc.file_path)}
                  >
                    Download
                  </Button>
                </Box>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LoanApplications; 
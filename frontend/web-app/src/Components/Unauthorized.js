import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

export default function Unauthorized() {
    function handleRedirectToLogin() {
        let location = window.location.href
        let loginUrl = location.replace("app.", "auth.")
        window.location.assign(loginUrl)
    }
    return (
        <div>
            <Button variant="outlined" onClick={handleRedirectToLogin}>
                Unauthorized
            </Button>
            <Dialog
                open={true}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    {"Unauthorized"}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        You have either not logged in or your token has expired. Please login again. 
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleRedirectToLogin}>OK</Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}

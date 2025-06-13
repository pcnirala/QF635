import React, {useState} from "react";
import {
    Button,
    Card,
    CardContent,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    Stack,
    Typography
} from '@mui/material';
import {COLORS} from "../theme/TableStyles";
import {REST_API_BASE_URL} from '../Config';

export default function AdminPanel({isLoggedIn, isTradingEnginePaused, setIsTradingEnginePaused}) {
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogContent, setDialogContent] = useState("");
    const [dialogTitle, setDialogTitle] = useState("Info");

    const handleDashboardReset = async () => {
        try {
            const response = await fetch(`${REST_API_BASE_URL}/api/reset-dashboard`, {
                method: "POST",
                headers: {"Content-Type": "application/json",},
                // body: JSON.stringify({ key: "value" }), // for sending data
            });
            const data = await response.json();
            console.log("API Response:", data);
            // Show MUI dialog
            setDialogContent(data.status);
            setDialogTitle("Dashboard Reset")
            setDialogOpen(true);
        } catch (error) {
            console.error("Error calling dashboard reset API:", error);
            setDialogContent("Failed to reset dashboard.");
            setDialogTitle("Dashboard Reset")
            setDialogOpen(true);
        }
    };

    const handleTradingEnginePause = async () => {
        try {
            const response = await fetch(`${REST_API_BASE_URL}/api/pause-trading-engine`, {
                method: "POST", headers: {"Content-Type": "application/json",},
            });
            const data = await response.json();
            setIsTradingEnginePaused(true);
            console.log("API Response:", data);
            setDialogContent(data.status);
            setDialogTitle("Pause Trading Engine")
            setDialogOpen(true);
        } catch (error) {
            console.error("Error calling pause API:", error);
            setDialogContent("Failed to pause trading engine.");
            setDialogTitle("Pause Trading Engine")
            setDialogOpen(true);
        }
    };

    const handleTradingEngineResume = async () => {
        try {
            const response = await fetch(`${REST_API_BASE_URL}/api/resume-trading-engine`, {
                method: "POST", headers: {"Content-Type": "application/json",},
            });
            const data = await response.json();
            setIsTradingEnginePaused(false);
            console.log("API Response:", data);
            setDialogContent(data.status);
            setDialogTitle("Resume Trading Engine")
            setDialogOpen(true);
        } catch (error) {
            console.error("Error calling resume API:", error);
            setDialogContent("Failed to resume trading engine.");
            setDialogTitle("Resume Trading Engine")
            setDialogOpen(true);
        }
    };

    return (
        <>
            <Card sx={{mt: 2}}>
                <CardContent>
                    <Typography variant="h6" sx={{mb: 2, color: COLORS.SCIS_GOLD, fontWeight: "bold"}}>
                        Admin Panel</Typography>

                    <Divider sx={{my: 2}}/>
                    <Stack direction="row" spacing={6}>
                        <Button variant="contained" fullWidth disabled={!isLoggedIn}
                                sx={{backgroundColor: COLORS.SOA_RED, color: COLORS.WHITE}}
                                onClick={handleDashboardReset}>Reset All Data On Dashboard</Button>
                    </Stack>

                    <Divider sx={{my: 3}}/>
                    <Stack direction="row" spacing={6}>
                        <Button variant="contained" disabled={isTradingEnginePaused || !isLoggedIn}
                                sx={{backgroundColor: COLORS.SCIS_GOLD, color: COLORS.WHITE}}
                                onClick={handleTradingEnginePause}>Pause Trading Engine</Button>
                        <Button variant="contained" disabled={!isTradingEnginePaused || !isLoggedIn}
                                sx={{backgroundColor: COLORS.LKCSB_BLUE, color: COLORS.WHITE}}
                                onClick={handleTradingEngineResume}>Resume Trading Engine</Button>
                    </Stack>
                </CardContent>
            </Card>

            {/* Material UI Dialog */}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle fontWeight="bold" color={COLORS.SCIS_GOLD}>{dialogTitle}</DialogTitle>
                <DialogContent dividers>
                    <Typography component="pre" variant="h6" fontWeight="bold" color={COLORS.SMU_BLUE} align="center">
                        {dialogContent}!
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)} color="primary" variant="contained">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}

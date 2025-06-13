import React, {useEffect, useState} from 'react';
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Paper,
    TextField,
    Typography
} from "@mui/material";
import {COLORS} from "../theme/TableStyles";
import Stack from '@mui/material/Stack';
import {REST_API_BASE_URL} from "../Config";

// If in public/ folder of project
const logoPath = process.env.PUBLIC_URL + "/LogoThinNoBG.png";

const format_options = {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZoneName: 'short'
};

export default function DashboardHeader({isLoggedIn, setIsLoggedIn, setIsTradingEnginePaused}) {
    // State to hold current date/time string
    const [now, setNow] = useState(() => new Date().toLocaleString('en-SG', format_options));

    const [loginDialogOpen, setLoginDialogOpen] = useState(false);
    const [loginError, setLoginError] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    useEffect(() => {
        const timer = setInterval(() => {
            setNow(new Date().toLocaleString('en-SG', format_options));
        }, 1000);

        return () => clearInterval(timer);  // Clean up on unmount
    }, []);

    const login_logout = () => {
        if (!isLoggedIn) {
            setLoginDialogOpen(true);
        } else {
            setIsLoggedIn(false);
            console.log("Logged out");
        }
    };

    const handleLoginSubmit = async () => {
        if (!username.trim() || !password.trim()) {
            setLoginError("Username and/or password cannot be empty.");
            return;
        }
        try {
            const response = await fetch(`${REST_API_BASE_URL}/api/login`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password}),
            });

            if (response.ok) {
                const login_response = await response.json();
                console.log("Login success:", login_response);
                setIsLoggedIn(true);
                setIsTradingEnginePaused(login_response.is_trading_engine_paused)
                setLoginDialogOpen(false);
                setLoginError(""); // Clear errors
                setPassword("");
            } else {
                const err = await response.json();
                setLoginError("Login failed: " + err.detail);
            }
        } catch (error) {
            console.error("Login error:", error);
            setLoginError("Login failed: " + error.message);
        }
    };


    return (
        <>
            <Box sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mt: 2, mb: 2
            }}>

                {/* Left group: logo + title */}
                <Box sx={{display: "flex", alignItems: "center"}}>
                    <img
                        src={logoPath}
                        alt="Accelerate Your Trading"
                        style={{
                            height: "48px",
                            objectFit: "contain"
                        }}/>

                    <Typography variant="h4">
                        <span style={{color: COLORS.LKCSB_BLUE, fontWeight: "bold"}}>Trade</span>
                        <span style={{color: COLORS.SCIS_GOLD, fontWeight: "bold"}}>Blaze</span>
                        <span style={{color: COLORS.SMU_BLUE, fontWeight: 300}}> Dashboard</span>
                    </Typography>
                </Box>

                {/* Right: datetime */}
                <Stack direction="row" spacing={2} alignItems="center">
                    <Paper sx={{p: 0.5}}>
                        <Typography variant="h6">
                            <span style={{color: COLORS.SMU_BLUE, fontWeight: "bold"}}>{now}</span>
                        </Typography>
                    </Paper>
                    <Button variant="contained" size="medium"
                            sx={{
                                backgroundColor: COLORS.SCIS_GOLD,
                                color: COLORS.WHITE,
                                fontWeight: "bold",
                                width: '6rem'
                            }}
                            onClick={login_logout}>{isLoggedIn ? "Logout" : "Login"}</Button>
                </Stack>
            </Box>

            <Dialog open={loginDialogOpen}
                    onClose={() => {
                        setLoginDialogOpen(false);
                        setLoginError("");     // Clear error message
                        setPassword("");
                    }}
                    maxWidth="xs" fullWidth>
                <DialogTitle fontWeight="bold" color={COLORS.SCIS_GOLD}>User Login</DialogTitle>
                <DialogContent dividers>
                    <TextField fontWeight="bold"
                               label="Username"
                               fullWidth
                               margin="normal"
                               value={username}
                               onChange={(e) => setUsername(e.target.value)}
                               InputProps={{sx: {color: COLORS.SMU_BLUE, fontWeight: "bold"}}}/>
                    <TextField
                        label="Password"
                        type="password"
                        fullWidth
                        margin="normal"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        InputProps={{sx: {color: COLORS.SMU_BLUE, fontWeight: "bold"}}}/>
                    {loginError && (
                        <Typography variant="body2" color={COLORS.SOA_RED} fontWeight="bold"
                                    sx={{mt: 1}}>{loginError}</Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button variant="contained" color="primary"
                            onClick={() => {
                                setLoginDialogOpen(false);
                                setLoginError("");
                                setPassword("");
                            }}>
                        Cancel
                    </Button>
                    <Button variant="contained" sx={{backgroundColor: COLORS.SCIS_GOLD}}
                            onClick={handleLoginSubmit}>
                        Login
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}

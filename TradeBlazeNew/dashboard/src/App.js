import React, {useState} from "react";
import './App.css';

import {Container, Grid, Paper} from "@mui/material";
import useWebSocket from "./hooks/UseWebSocket";
import DashboardHeader from "./components/DashboardHeader";
import MarketDataTable from "./components/MarketDataTable";
import SignalsTable from "./components/SignalsTable";
import OrdersTable from "./components/OrdersTable";
import {CollapsibleTrades} from "./components/TradesTable";
import PositionsTable from "./components/PositionsTable";
import PerformancePanel from "./components/PerformancePanel";
import AdminPanel from "./components/AdminPanel";

import {WS_API_BASE_URL} from './Config';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isTradingEnginePaused, setIsTradingEnginePaused] = useState(false);

    const liveData = useWebSocket(`${WS_API_BASE_URL}/ws/livefeed`);

    // liveData = {ticks: [], signals: [], orders: [], trades: [],
    // positions: [], pnl: ..., drawdown: ..., var: ...}
    return (
        <Container maxWidth="xl" sx={{mt: 2}}>
            <DashboardHeader isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn}
                             setIsTradingEnginePaused={setIsTradingEnginePaused}/>
            <Grid container spacing={2}>
                <Grid item xs={12} md={8}>
                    <Paper sx={{p: 2, mb: 2}}>
                        <MarketDataTable rows={liveData?.market_data_ticks || []}/>
                    </Paper>
                    <Paper sx={{p: 2, mb: 2}}>
                        <SignalsTable rows={liveData?.signals || []}/>
                    </Paper>
                    <Paper sx={{p: 2, mb: 2}}>
                        <OrdersTable rows={liveData?.orders || []}/>
                    </Paper>
                    <Paper sx={{p: 2, mb: 2}}>
                        <CollapsibleTrades rows={liveData?.trades || []}/>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{p: 2, mb: 2}}>
                        <PositionsTable rows={liveData?.positions || []}/>
                    </Paper>
                    <PerformancePanel
                        realized_pnl={liveData?.realized_pnl}
                        unrealized_pnl={liveData?.unrealized_pnl}
                        pnl_std_dev={liveData?.pnl_std_dev}
                        sharp_ratio={liveData?.sharp_ratio}
                        treynor_ratio={liveData?.treynor_ratio}
                        information_ratio={liveData?.information_ratio}
                        drawdown={liveData?.drawdown}
                        max_drawdown={liveData?.max_drawdown}
                        cagr={liveData?.cagr}
                        var_value={liveData?.var_value}
                    />
                    <AdminPanel isLoggedIn={isLoggedIn} isTradingEnginePaused={isTradingEnginePaused}
                                setIsTradingEnginePaused={setIsTradingEnginePaused}/>
                </Grid>
            </Grid>
        </Container>
    );
}

export default App;

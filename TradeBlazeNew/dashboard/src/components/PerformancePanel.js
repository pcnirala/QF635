// src/components/PerformancePanel.js
import React from "react";
import {Card, CardContent, Divider, Typography} from "@mui/material";
import {COLORS} from "../theme/TableStyles";

export default function PerformancePanel({
                                             realized_pnl, unrealized_pnl, pnl_std_dev,
                                             sharp_ratio, treynor_ratio, information_ratio,
                                             drawdown, max_drawdown, cagr, var_value
                                         }) {
    return (
        <Card sx={{mt: 2}}>
            <CardContent>
                <Typography variant="h6" sx={{color: COLORS.SCIS_GOLD, fontWeight:"bold"}}>Performance Metrics</Typography>
                <Divider sx={{my: 1}}/> {/* Horizontal line with vertical spacing */}

                <Typography style={{fontWeight: "bold", color: COLORS.SMU_BLUE}}>
                    Realized PnL: {realized_pnl}<br/>
                    Unrealized PnL: {unrealized_pnl}<br/>
                    PnL Std Dev: {pnl_std_dev}<br/>
                    Sharp Ratio: {sharp_ratio}<br/>
                    Treynor Ratio: {treynor_ratio}<br/>
                    Information Ratio: {information_ratio}<br/>
                    Drawdown: {drawdown}<br/>
                    Max Drawdown: {max_drawdown}<br/>
                    CAGR: {cagr}<br/>
                    VaR: {var_value}
                </Typography>
            </CardContent>
        </Card>
    );
}

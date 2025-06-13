// src/components/MarketDataTable.js
import React from "react";
import {Table, TableBody, TableCell, TableHead, TableRow, Typography} from "@mui/material";
import {cellStyle, COLORS, headerStyle, tableStyle} from "../theme/TableStyles";

export default function PositionsTable({rows}) {
    return (
        <>
            <Typography variant="h6" sx={{color: COLORS.SCIS_GOLD, fontWeight:"bold"}}>Positions Data</Typography>
            <Table style={tableStyle}>
                <TableHead>
                    <TableRow>
                        <TableCell style={headerStyle}>Timestamp</TableCell>
                        <TableCell style={headerStyle}>Ticker</TableCell>
                        <TableCell style={headerStyle}>Units</TableCell>
                        <TableCell style={headerStyle}>Avg Price</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row, idx) => (
                        <TableRow key={idx}>
                            <TableCell style={cellStyle}>{row.timestamp?.slice(11)}</TableCell>
                            <TableCell style={cellStyle}>{row.ticker}</TableCell>
                            <TableCell style={cellStyle}>{row.units}</TableCell>
                            <TableCell style={cellStyle}>{row.avg_unit_price}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </>
    );
}

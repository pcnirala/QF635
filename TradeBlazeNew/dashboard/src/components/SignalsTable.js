// src/components/MarketDataTable.js
import React from "react";
import {Table, TableBody, TableCell, TableHead, TableRow, Typography} from "@mui/material";
import {cellStyle, COLORS, headerStyle, tableStyle} from "../theme/TableStyles";

export default function SignalsTable({rows}) {
    return (
        <>
            <Typography variant="h6" sx={{color: COLORS.SCIS_GOLD, fontWeight:"bold"}}>Signals Data</Typography>
            <Table style={tableStyle}>
                <TableHead>
                    <TableRow>
                        <TableCell style={headerStyle}>Timestamp</TableCell>
                        <TableCell style={headerStyle}>Ticker</TableCell>
                        <TableCell style={headerStyle}>Price</TableCell>
                        <TableCell style={headerStyle}>Action</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row, idx) => (
                        <TableRow key={idx} sx={{
                            backgroundColor: idx % 2 === 0 ? COLORS.WHITE : COLORS.SMU_GOLD_BK // light gray shade for odd rows
                        }}>
                            <TableCell style={cellStyle}>{row.timestamp?.slice(11)}</TableCell>
                            <TableCell style={cellStyle}>{row.ticker}</TableCell>
                            <TableCell style={cellStyle}>{row.price}</TableCell>
                            <TableCell style={cellStyle}>{row.action}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </>
    );
}

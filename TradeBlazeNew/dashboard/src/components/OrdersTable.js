// src/components/MarketDataTable.js
import React from "react";
import {Table, TableBody, TableCell, TableHead, TableRow, Typography} from "@mui/material";
import {cellStyle, COLORS, headerStyle, tableStyle} from "../theme/TableStyles";

export default function OrdersTable({rows}) {
    return (
        <>
            <Typography variant="h6" sx={{color: COLORS.SCIS_GOLD, fontWeight:"bold"}}>Orders Data</Typography>
            <Table style={tableStyle}>
                <TableHead>
                    <TableRow>
                        <TableCell style={headerStyle}>Timestamp</TableCell>
                        <TableCell style={headerStyle}>Ticker</TableCell>
                        <TableCell style={headerStyle}>Side</TableCell>
                        <TableCell style={headerStyle}>Qty</TableCell>
                        <TableCell style={headerStyle}>Order Status</TableCell>
                        <TableCell style={headerStyle}>Filled Price</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row, idx) => (
                        <TableRow key={idx} sx={{
                            backgroundColor: idx % 2 === 0 ? COLORS.WHITE : COLORS.SMU_GOLD_BK // light gray shade for odd rows
                        }}>
                            <TableCell style={cellStyle}>{row.timestamp?.slice(11)}</TableCell>
                            <TableCell style={cellStyle}>{row.ticker}</TableCell>
                            <TableCell style={cellStyle}>{row.side}</TableCell>
                            <TableCell style={cellStyle}>{row.qty}</TableCell>
                            <TableCell style={cellStyle}>{row.order_status}</TableCell>
                            <TableCell style={cellStyle}>{row.filled_price}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </>
    );
}

// src/components/MarketDataTable.js
import React, {useState} from "react";
import {Button, Collapse, Table, TableBody, TableCell, TableHead, TableRow, Typography} from "@mui/material";

import {cellStyle, COLORS, headerStyle, tableStyle} from "../theme/TableStyles";


export function TradesTable({rows}) {
    return (
        <>
            <Typography variant="h6" sx={{color: COLORS.SCIS_GOLD, fontWeight: "bold"}}>Trades Data</Typography>
            <Table style={tableStyle}>
                <TableHead>
                    <TableRow>
                        <TableCell style={headerStyle}>Timestamp</TableCell>
                        <TableCell style={headerStyle}>Ticker</TableCell>
                        <TableCell style={headerStyle}>Direction</TableCell>
                        <TableCell style={headerStyle}>Units</TableCell>
                        <TableCell style={headerStyle}>Unit Price</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row, idx) => (
                        <TableRow key={idx} sx={{
                            backgroundColor: idx % 2 === 0 ? COLORS.WHITE : COLORS.SMU_GOLD_BK // light gray shade for odd rows
                        }}>
                            <TableCell style={cellStyle}>{row.timestamp?.slice(11)}</TableCell>
                            <TableCell style={cellStyle}>{row.ticker}</TableCell>
                            <TableCell style={cellStyle}>{row.direction}</TableCell>
                            <TableCell style={cellStyle}>{row.units}</TableCell>
                            <TableCell style={cellStyle}>{row.unit_price}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </>
    );
}

export function CollapsibleTrades({rows}) {
    const [open, setOpen] = useState(true);

    return (
        <>
            <Button onClick={() => setOpen(o => !o)}>
                {open ? "Hide" : "Show"} Trades
            </Button>
            <Collapse in={open} timeout="auto" unmountOnExit>
                <TradesTable rows={rows}/>
            </Collapse>
        </>
    );
}

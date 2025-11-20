"use client";

import { useEffect, useMemo, useState } from "react";
import type { ElementType } from "react";
import { Coins } from "lucide-react";

import { StatsCard } from "@/components/blocks/stats-card";
import api from "@/lib/api";

export interface TonBalanceCardProps {
  endpoint?: string;
  label?: string;
  description?: string;
  icon?: ElementType;
}

interface TonBalanceResponse {
  balance?: string | number;
  currency?: string;
}

export function TonBalanceCard({
  endpoint = "/ton/balance",
  label = "TON Balance",
  description = "Real-time treasury funds secured on-chain",
  icon = Coins,
}: TonBalanceCardProps) {
  const [balance, setBalance] = useState<string>("—");
  const [trend, setTrend] = useState<{ direction: "up" | "down"; value: string } | undefined>();

  useEffect(() => {
    let isMounted = true;

    const fetchBalance = async () => {
      try {
        const response = await api.get<TonBalanceResponse>(endpoint);
        if (!isMounted) return;

        const rawBalance = response.data.balance ?? "0";
        const numeric = Number(rawBalance);
        const formatted = Number.isFinite(numeric) ? numeric.toFixed(4) : String(rawBalance);
        const currency = response.data.currency ? ` ${response.data.currency}` : " TON";

        setTrend({ direction: "up", value: "+0.00%" });
        setBalance(`${formatted}${currency}`);
      } catch (err) {
        if (!isMounted) return;
        setBalance("Unavailable");
        setTrend(undefined);
      }
    };

    fetchBalance();
  }, [endpoint]);

  const iconToRender = useMemo(() => icon, [icon]);

  return <StatsCard label={label} value={balance} description={description} icon={iconToRender} trend={trend} />;
}

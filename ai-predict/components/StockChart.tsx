import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, IChartApi, Time, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts';
import { StockDataPoint } from '../types';

interface ChartColors {
  backgroundColor?: string;
  lineColor?: string;
  textColor?: string;
  areaTopColor?: string;
  areaBottomColor?: string;
}

interface StockChartProps {
  data: StockDataPoint[];
  colors?: ChartColors;
}

const StockChart: React.FC<StockChartProps> = ({ data, colors = {} as ChartColors }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const handleResize = () => {
      chartRef.current?.applyOptions({ width: chartContainerRef.current?.clientWidth });
    };

    const {
      backgroundColor = 'transparent',
      textColor = '#333',
    } = colors;

    // Create Chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: backgroundColor },
        textColor,
      },
      width: chartContainerRef.current.clientWidth,
      height: 600,
      grid: {
        vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
        horzLines: { color: 'rgba(197, 203, 206, 0.5)' },
      },
    });
    chartRef.current = chart;

    // --- Main Series (Candlestick) ---
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#EF5350', // Red for up (Taiwan style)
      downColor: '#26A69A', // Green for down (Taiwan style)
      borderVisible: false,
      wickUpColor: '#EF5350',
      wickDownColor: '#26A69A',
    });

    const candlestickData = data.map(d => ({
      time: d.date as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.price,
    }));
    candlestickSeries.setData(candlestickData);

    // --- Bollinger Bands ---
    // Upper
    const bbUpperSeries = chart.addSeries(LineSeries, {
      color: 'rgba(0, 150, 255, 0.5)',
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: 'BB Upper',
    });
    const bbUpperData = data
      .filter(d => d.bb_upper !== undefined)
      .map(d => ({ time: d.date as Time, value: d.bb_upper! }));
    bbUpperSeries.setData(bbUpperData);

    // Lower
    const bbLowerSeries = chart.addSeries(LineSeries, {
      color: 'rgba(0, 150, 255, 0.5)',
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: 'BB Lower',
    });
    const bbLowerData = data
      .filter(d => d.bb_lower !== undefined)
      .map(d => ({ time: d.date as Time, value: d.bb_lower! }));
    bbLowerSeries.setData(bbLowerData);

    // Middle
    const bbMiddleSeries = chart.addSeries(LineSeries, {
      color: 'rgba(255, 165, 0, 0.8)', // Orange
      lineWidth: 1,
      title: 'BB Middle',
    });
    const bbMiddleData = data
      .filter(d => d.bb_middle !== undefined)
      .map(d => ({ time: d.date as Time, value: d.bb_middle! }));
    bbMiddleSeries.setData(bbMiddleData);


    // --- Volume (Separate Pane) ---
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '', // Set as an overlay
    });

    // Configure the main price scale to leave space for volume
    chart.priceScale('right').applyOptions({
      scaleMargins: {
        top: 0.1,
        bottom: 0.3, // Reserve bottom 30% for volume
      },
    });

    // Configure the overlay price scale for volume
    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.7, // Volume takes up the bottom 30%
        bottom: 0,
      },
    });

    const volumeData = data.map(d => ({
      time: d.date as Time,
      value: d.volume,
      color: d.price >= d.open ? 'rgba(239, 83, 80, 0.5)' : 'rgba(38, 166, 154, 0.5)',
    }));
    volumeSeries.setData(volumeData);


    // --- RSI (Separate Scale) ---
    const rsiSeries = chart.addSeries(LineSeries, {
      color: '#A020F0', // Purple
      lineWidth: 2,
      priceScaleId: 'left',
      title: 'RSI',
    });

    const rsiData = data
      .filter(d => d.rsi !== undefined)
      .map(d => ({ time: d.date as Time, value: d.rsi! }));
    rsiSeries.setData(rsiData);

    chart.priceScale('left').applyOptions({
      visible: false, // Hide left scale to avoid clutter
    });

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, colors]);

  return (
    <div className="w-full h-full p-4 rounded-xl">
      <div ref={chartContainerRef} className="w-full h-[500px]" />
    </div>
  );
};

export default StockChart;
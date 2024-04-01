import React, { useState, useEffect } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios'; // Import axios for making HTTP requests

const CandlestickChart = (props) => {
  const { api, kwargs = {} } = props;
  const {
    symbols = ['AAPL', 'GOOGL'], // Default symbols
    api_key,
    api_source,
    height = 400,
    width = 800,
  } = kwargs;

  const [symbol, setSymbol] = useState(symbols[0]); // Default symbol
  const [interval, setInterval] = useState('1D'); // Default interval

  useEffect(() => {
    fetchChartData();
  }, [symbol, interval]);

  const fetchChartData = async () => {
    try {
      const body = {
        api_key: api_key,
        symbol: symbol,
        interval: interval,
      };
      const { data } = await axios.post(api_source, body);
      renderChart(data);
    } catch (error) {
      console.error('Error fetching chart data:', error);
    }
  };

  const renderChart = (data) => {
    const chart = createChart(document.getElementById('chart'), {
      width: width,
      height: height,
    });

    const candleSeries = chart.addCandlestickSeries();

    candleSeries.setData(data);
  };

  const handleSymbolChange = (event) => {
    setSymbol(event.target.value);
  };

  const handleIntervalChange = (event) => {
    setInterval(event.target.value);
  };

  return (
    <div>
      <div>
        <label htmlFor="symbol">Symbol:</label>
        <select id="symbol" value={symbol} onChange={handleSymbolChange}>
          {symbols.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="interval">Interval:</label>
        <select id="interval" value={interval} onChange={handleIntervalChange}>
          <option value="1D">1D</option>
          <option value="1W">1W</option>
          <option value="1M">1M</option>
          {/* Add more intervals as needed */}
        </select>
      </div>
      <div id="chart"></div>
    </div>
  );
};

export default CandlestickChart;
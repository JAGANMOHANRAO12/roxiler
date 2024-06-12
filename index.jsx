import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [month, setMonth] = useState('March');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [transactions, setTransactions] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [barChart, setBarChart] = useState({});
  const [pieChart, setPieChart] = useState({});

  useEffect(() => {
    fetchTransactions();
    fetchStatistics();
    fetchBarChart();
    fetchPieChart();
  }, [month, search, page]);

  const fetchTransactions = async () => {
    const response = await axios.get('/transactions', {
      params: { month, search, page }
    });
    setTransactions(response.data.transactions);
  };

  const fetchStatistics = async () => {
    const response = await axios.get('/statistics', { params: { month } });
    setStatistics(response.data);
  };

  const fetchBarChart = async () => {
    const response = await axios.get('/bar_chart', { params: { month } });
    setBarChart(response.data);
  };

  const fetchPieChart = async () => {
    const response = await axios.get('/pie_chart', { params: { month } });
    setPieChart(response.data);
  };

  return (
    <div>
      <select value={month} onChange={(e) => setMonth(e.target.value)}>
      </select>
     </div>)
}
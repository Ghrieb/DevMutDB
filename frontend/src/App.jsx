// SPDX-FileCopyrightText: 2025 Abdelkarim Hani Ghrieb
// SPDX-License-Identifier: LicenseRef-Proprietary

import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Search from './pages/Search';
import Results from './pages/Results';
import Methodology from './pages/Methodology';
import ApiDocs from './pages/ApiDocs';
import GetStarted from './pages/GetStarted';
import ScientificFooter from './components/ScientificFooter';

export default function App() {
  const [scoreResult, setScoreResult] = useState(null);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={<Search onScoreComplete={setScoreResult} />}
        />
        <Route
          path="/results"
          element={<Results result={scoreResult} />}
        />
        <Route
          path="/methodology"
          element={<Methodology />}
        />
        <Route
          path="/api"
          element={<ApiDocs />}
        />
        <Route
          path="/get-started"
          element={<GetStarted />}
        />
      </Routes>
      <ScientificFooter />
    </Router>
  );
}

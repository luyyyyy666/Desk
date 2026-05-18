import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import Generate from './pages/Generate';
import QuestionBank from './pages/QuestionBank';
import Practice from './pages/Practice';
import ErrorBook from './pages/ErrorBook';
import Analytics from './pages/Analytics';
import ExportPage from './pages/ExportPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/generate" replace />} />
        <Route path="generate" element={<Generate />} />
      <Route path="bank" element={<QuestionBank />} />
        <Route path="practice" element={<Practice />} />
        <Route path="errors" element={<ErrorBook />} />
        <Route path="analytics" element={<Analytics />} />
      <Route path="export" element={<ExportPage />} />
      </Route>
    </Routes>
  );
}

export default App;

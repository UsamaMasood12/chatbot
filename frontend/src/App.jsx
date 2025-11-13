import React, { lazy, Suspense } from 'react';
import './styles/index.css';

// Lazy load ChatBot component
const ChatBot = lazy(() => import('./components/ChatBot'));

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Your existing portfolio content goes here */}
      <div className="container mx-auto p-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Usama Masood - Portfolio
        </h1>
        <p className="text-lg text-gray-600">
          Data Scientist | AI & ML Engineer
        </p>
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-700">
            Welcome to my portfolio! Feel free to explore my work and projects.
            You can also chat with my AI assistant in the bottom-right corner to learn more about my experience and skills.
          </p>
        </div>
      </div>

      {/* Lazy loaded ChatBot Widget with loading fallback */}
      <Suspense fallback={<div></div>}>
        <ChatBot />
      </Suspense>
    </div>
  );
}

export default App;

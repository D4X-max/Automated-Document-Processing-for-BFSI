import React from 'react';

function Header() {
  return (
    <header className="bg-gray-800 text-white shadow-md">
      <div className="container mx-auto px-6 py-4">
        <h1 className="text-2xl font-bold">Automated Document Processor</h1>
        <p className="text-sm text-gray-400">KYC & Document Automation for BFSI</p>
      </div>
    </header>
  );
}

export default Header;

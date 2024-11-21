"use client";
import React, { useEffect, useState } from "react";

const Page = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:3000/api/predict");
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const result = await response.json();
        setData(result);
      } catch (err) {}
    };

    fetchData();
  }, []);

  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h1>Inventory Data</h1>
      <pre>{data ? JSON.stringify(data, null, 2) : "Loading..."}</pre>
    </div>
  );
};

export default Page;

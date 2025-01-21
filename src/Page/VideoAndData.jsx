import React, { useEffect, useState } from "react";
import axios from "axios";

const VideoAndData = () => {
  const [data, setData] = useState({
    total: 0,
    person_count: 0,
    mask_count: 0,
    vest_count: 0,
  });

  useEffect(() => {
    // Fetch data every second
    const interval = setInterval(() => {
      axios
        .get("http://127.0.0.1:5000/get_data")
        .then((response) => {
          setData(response.data);
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
        });
    }, 1000);

    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  return (
    <div style={{ textAlign: "center" }}>
      <h1>Video and Data Dashboard</h1>

      {/* Video Feed */}
      <div>
        <h2>Live Video Feed</h2>
        <img
          src="http://127.0.0.1:5000/video_feed"
          alt="Live Feed"
          style={{ width: "640px", height: "480px", border: "2px solid black" }}
        />
      </div>

      {/* Data Display */}
      <div style={{ marginTop: "20px" }}>
        <h2>Data Information</h2>
        <p>
          <strong>Total People:</strong> {data.total}
        </p>
        <p>
          <strong>Person Count:</strong> {data.person_count}
        </p>
        <p>
          <strong>Mask Count (%):</strong> {data.mask_count}
        </p>
        <p>
          <strong>Vest Count (%):</strong> {data.vest_count}
        </p>
      </div>
    </div>
  );
};

export default VideoAndData;

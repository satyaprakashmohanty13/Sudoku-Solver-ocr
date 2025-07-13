// api/solve.js
// This serverless function acts as a proxy to forward image upload requests
// to the actual backend API, keeping the backend URL hidden from the client.

export default async function handler(req, res) {
  // Ensure the request method is POST
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ message: `Method ${req.method} Not Allowed` });
  }

  // Get the real backend URL from environment variables
  // In Vercel, you would set BACKEND_URL as an environment variable.
  const backendUrl = process.env.BACKEND_URL;

  // Check if the backend URL is configured
  if (!backendUrl) {
    console.error('BACKEND_URL environment variable is not set.');
    return res.status(500).json({ message: 'Server configuration error: Backend URL is not defined.' });
  }

  try {
    // Forward the request to the real backend
    // We need to pass the incoming request's body and headers (especially Content-Type)
    // directly to the backend fetch call.
    // req.body in Vercel's Node.js runtime for multipart/form-data is a ReadableStream.
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      // Pass the original headers from the client, especially 'Content-Type'
      // which contains the boundary for multipart/form-data.
      headers: {
        'Content-Type': req.headers['content-type'],
      },
      // Pass the raw body stream directly.
      body: req, // Vercel's `req` object is a Node.js IncomingMessage, which is a ReadableStream
    });

    // Check if the request to the backend was successful
    if (!backendResponse.ok) {
      // If the backend returned an error, try to parse its message
      let errorData = {};
      try {
        errorData = await backendResponse.json();
      } catch (parseError) {
        // If parsing fails, just use the status text
        errorData.message = backendResponse.statusText;
      }
      console.error(`Backend error: ${backendResponse.status} - ${errorData.message || 'Unknown error'}`);
      return res.status(backendResponse.status).json({
        message: errorData.message || `Backend responded with status: ${backendResponse.status}`,
        details: errorData // Include any details from the backend error
      });
    }

    // Parse the JSON response from the backend
    const data = await backendResponse.json();

    // Send the backend's response back to the client
    return res.status(200).json(data);

  } catch (error) {
    // Handle any network errors or unexpected issues during the proxying
    console.error('Proxy error:', error);
    return res.status(500).json({ message: 'An error occurred while processing your request.', error: error.message });
  }
}


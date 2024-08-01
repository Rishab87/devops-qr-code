export async function POST(req) {
  return await handleProxy(req);
}

async function handleProxy(req) {

  const body = await req.json();
  const {url} = body;
  //use /backend/ instead of /backend-service/ for development
  const backendUrl = `http://backend-service:8000/generate-qr/?${url}`;

  const response = await fetch(backendUrl , {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    return {
      status: response.status,
      body: await response.text(),
    };
  }

  const data = await response.json();
  return data.data.qr_code_url;
  
}

export async function POST(req) {
  return await handleProxy(req);
}

async function handleProxy(req) {

  const body = await req.json();
  const {url} = body;
  const backendUrl = `http://backend-service/generate-qr/?${url}`;

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

import axios from 'axios';

interface SourceResponse {
  errors: null;
  message: string;
  requestId: string;
  result: {
    name: string;
    domain: string;
    id: string;
  }[];
  success: boolean;
}

export async function fetchSources() {
  const res = await axios.get<SourceResponse>('http://localhost:8000/api/v1/sources/');
  console.log(res);
  return res.data.result; // теперь TypeScript знает структуру
}

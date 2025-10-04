import axios from 'axios';

interface CategoryResponse {
  errors: null;
  message: string;
  requestId: string;
  result: {
    name: string;
    id: string;
  }[];
  success: boolean;
}

export async function fetchCategories() {
  const res = await axios.get<CategoryResponse>('http://localhost:8000/api/v1/categories/');
  console.log(res);
  return res.data.result; // теперь TypeScript знает структуру
}

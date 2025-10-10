interface ApiResponse<T = any> {
  errors: null | string | string[] | { [key: string]: string };
  message: string;
  requestId: string;
  result: T;
  success: boolean;
}

import { createClient } from '@connectrpc/connect';
import { createGrpcWebTransport } from '@connectrpc/connect-web';
import { AuthService } from './gen/auth_connect';


const apiUrl = 'http://localhost:8080';

const transport = createGrpcWebTransport({
  baseUrl: apiUrl,
});

export const authClient = createClient(AuthService, transport);
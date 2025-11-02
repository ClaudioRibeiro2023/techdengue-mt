/**
 * Keycloak Authentication Service
 */
import { User, UserManager, WebStorageStateStore } from 'oidc-client-ts';

const KEYCLOAK_URL = import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080';
const KEYCLOAK_REALM = import.meta.env.VITE_KEYCLOAK_REALM || 'techdengue';
const KEYCLOAK_CLIENT_ID = import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'techdengue-frontend';

const config = {
  authority: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}`,
  client_id: KEYCLOAK_CLIENT_ID,
  redirect_uri: `${window.location.origin}/callback`,
  post_logout_redirect_uri: `${window.location.origin}/`,
  response_type: 'code',
  scope: 'openid profile email',
  userStore: new WebStorageStateStore({ store: window.localStorage }),
  automaticSilentRenew: true,
  silent_redirect_uri: `${window.location.origin}/silent-renew.html`,
};

class AuthService {
  private userManager: UserManager;
  private user: User | null = null;

  constructor() {
    this.userManager = new UserManager(config);
    
    // Event listeners
    this.userManager.events.addUserLoaded((user) => {
      this.user = user;
      console.log('User loaded:', user.profile.email);
    });

    this.userManager.events.addUserUnloaded(() => {
      this.user = null;
      console.log('User unloaded');
    });

    this.userManager.events.addAccessTokenExpired(() => {
      console.log('Access token expired, attempting silent renew...');
      this.signinSilent();
    });

    this.userManager.events.addSilentRenewError((error) => {
      console.error('Silent renew error:', error);
      this.logout();
    });
  }

  /**
   * Inicia login redirecionando para Keycloak
   */
  async login(): Promise<void> {
    try {
      await this.userManager.signinRedirect();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Completa callback após login
   */
  async handleCallback(): Promise<User> {
    try {
      const user = await this.userManager.signinRedirectCallback();
      this.user = user;
      return user;
    } catch (error) {
      console.error('Callback error:', error);
      throw error;
    }
  }

  /**
   * Renovação silenciosa de token
   */
  async signinSilent(): Promise<User | null> {
    try {
      const user = await this.userManager.signinSilent();
      this.user = user;
      return user;
    } catch (error) {
      console.error('Silent signin error:', error);
      return null;
    }
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    try {
      await this.userManager.signoutRedirect();
      this.user = null;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }

  /**
   * Retorna usuário atual
   */
  async getUser(): Promise<User | null> {
    if (this.user && !this.user.expired) {
      return this.user;
    }

    try {
      const user = await this.userManager.getUser();
      this.user = user;
      return user;
    } catch (error) {
      console.error('Get user error:', error);
      return null;
    }
  }

  /**
   * Verifica se está autenticado
   */
  async isAuthenticated(): Promise<boolean> {
    const user = await this.getUser();
    return user !== null && !user.expired;
  }

  /**
   * Retorna access token
   */
  async getAccessToken(): Promise<string | null> {
    const user = await this.getUser();
    return user?.access_token || null;
  }

  /**
   * Retorna informações do perfil
   */
  async getProfile() {
    const user = await this.getUser();
    if (!user) return null;

    return {
      id: user.profile.sub,
      email: user.profile.email,
      name: user.profile.name,
      preferred_username: user.profile.preferred_username,
      roles: (user.profile.roles as string[]) || [],
      groups: (user.profile.groups as string[]) || [],
    };
  }

  /**
   * Verifica se usuário tem role específica
   */
  async hasRole(role: string): Promise<boolean> {
    const profile = await this.getProfile();
    if (!profile) return false;
    
    return profile.roles.includes(role);
  }

  /**
   * Verifica se usuário pertence a grupo específico
   */
  async hasGroup(group: string): Promise<boolean> {
    const profile = await this.getProfile();
    if (!profile) return false;
    
    return profile.groups.includes(group);
  }
}

// Singleton
export const authService = new AuthService();

// Helper para axios interceptor
export const getAuthHeader = async (): Promise<{ Authorization: string } | Record<string, never>> => {
  const token = await authService.getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

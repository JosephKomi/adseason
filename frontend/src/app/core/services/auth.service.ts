import { Injectable, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs';
import { LoginRequest, RegisterRequest, TokenResponse, User } from '../models/user.model';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = inject(ApiService);
  private router = inject(Router);

  currentUser = signal<User | null>(null);
  private accessToken = signal<string | null>(null);

  isLoggedIn() {
    return !!this.accessToken();
  }

  getAccessToken() {
    return this.accessToken();
  }

  login(body: LoginRequest) {
    return this.api.post<TokenResponse>('/api/auth/login', body).pipe(
      tap(res => {
        this.accessToken.set(res.access_token);
        this.loadMe();
      })
    );
  }

  register(body: RegisterRequest) {
    return this.api.post<User>('/api/auth/register', body);
  }

  loadMe() {
    this.api.get<User>('/api/auth/me').subscribe({
      next: user => this.currentUser.set(user),
      error: (err: HttpErrorResponse) => {
        if (err.status === 401) this.logout();
      },
    });
  }

  refreshToken() {
    return this.api.post<TokenResponse>('/api/auth/refresh', {}).pipe(
      tap(res => this.accessToken.set(res.access_token))
    );
  }

  logout() {
    this.api.post('/api/auth/logout', {}).subscribe();
    this.accessToken.set(null);
    this.currentUser.set(null);
    this.router.navigate(['/auth/login']);
  }
}

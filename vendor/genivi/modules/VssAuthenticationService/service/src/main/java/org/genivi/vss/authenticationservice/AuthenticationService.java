package org.genivi.vss.authenticationservice;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

import androidx.annotation.Nullable;

public class AuthenticationService extends Service {

    private IBinder mAuthenticationService;

    @Override
    public void onCreate() {
        mAuthenticationService = new IAuthenticationServiceImpl(getApplicationContext());
    }
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return mAuthenticationService;
    }
}

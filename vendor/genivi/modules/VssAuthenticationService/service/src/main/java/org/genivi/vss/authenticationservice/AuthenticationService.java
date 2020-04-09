// Copyright (C) 2020 TietoEVRY
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

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

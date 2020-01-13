package com.genivi.vss.vssservice;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

import androidx.annotation.Nullable;

public class VSSService extends Service {

    private IBinder mVSSService;

    @Override
    public void onCreate() {
        mVSSService = new IVSSServiceImpl(getApplicationContext());
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return mVSSService;
    }
}

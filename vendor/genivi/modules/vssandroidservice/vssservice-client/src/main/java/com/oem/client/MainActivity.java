package com.oem.client;

import androidx.appcompat.app.AppCompatActivity;

import android.content.ComponentName;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.os.RemoteException;
import android.util.Log;

import com.genivi.vss.vssservice.IVSSService;
import com.genivi.vss.vssservice.VSS;

public class MainActivity extends AppCompatActivity {

    public static final String TAG = MainActivity.class.getSimpleName();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        bindService(VSS.VSS_SERVICE_INTENT, new ServiceConnection() {
            @Override
            public void onServiceConnected(ComponentName name, IBinder service) {
                IVSSService mVssService = IVSSService.Stub.asInterface(service);
                try {
                    mVssService.getProperty(VSS.PROPERTY_GROUP_A_PROP1);
                } catch (RemoteException e) {
                    Log.e(TAG, "Exception while getting the property ", e);
                }
            }

            @Override
            public void onServiceDisconnected(ComponentName name) {

            }
        }, BIND_AUTO_CREATE);
    }


}

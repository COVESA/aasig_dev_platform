package org.genivi.vss.authenticationservice;

import androidx.appcompat.app.AppCompatActivity;

import android.content.ComponentName;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.os.RemoteException;

public class MainActivity extends AppCompatActivity {

    IAuthenticationService mAuthenticationService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // TODO Move this connection boilerplate to VSS-SDK since this code will be shared across the clients
        bindService(VSS.AUTHENTICATION_SERVICE_INTENT, new ServiceConnection() {
            @Override
            public void onServiceConnected(ComponentName name, IBinder service) {
                mAuthenticationService = IAuthenticationService.Stub.asInterface(service);
            }

            @Override
            public void onServiceDisconnected(ComponentName name) {
                mAuthenticationService = null;
            }
        }, BIND_AUTO_CREATE);

        // TODO connect "getAuthToken" to some controls
    }

    private String getAuthToken() throws RemoteException {
        return mAuthenticationService.getAuthenticationToken();
    }
}

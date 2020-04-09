package org.genivi.vss.authenticationservice;

import android.content.Context;
import android.os.RemoteException;

import java.util.ArrayList;
import java.util.List;

public class IAuthenticationServiceImpl extends IAuthenticationService.Stub {
    private final Context mContext;

    IAuthenticationServiceImpl(Context context) {
        mContext = context;
    }

    @Override
    public String getAuthenticationToken() throws RemoteException {
        List<String>  grantedPermissions = getGrantedPermissions();
        // TODO Generate JWT with fetched permisions
        return null;
    }

    private List<String> getGrantedPermissions() {
        // TODO Connect to PackageManager and retrieve permissions;
        return new ArrayList<String>();
    }
}

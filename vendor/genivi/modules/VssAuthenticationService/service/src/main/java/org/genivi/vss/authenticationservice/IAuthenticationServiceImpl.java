package org.genivi.vss.authenticationservice;

import android.os.RemoteException;

public class IAuthenticationServiceImpl extends IAuthenticationService.Stub {
    @Override
    public String getAuthenticationToken() throws RemoteException {
        // TODO Connect to PackageMAnager and generate token
        return null;
    }
}

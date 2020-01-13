package com.genivi.vss.vssservice;

import android.content.Context;
import android.content.pm.PackageManager;
import android.os.RemoteException;

public class IVSSServiceImpl extends IVSSService.Stub {
    private final Context mContext;

    public IVSSServiceImpl(Context applicationContext) {
        mContext = applicationContext;
    }

    @Override
    public String getProperty(String key) throws RemoteException {
        String requiredPermission = checkRequiredPermission(key);
        if (mContext.checkCallingOrSelfPermission(requiredPermission) == PackageManager.PERMISSION_GRANTED) {
          return "42"; // the value is not intresting for this POC
        } else {
            throw new SecurityException("Permission needed to access " + key);
        }
    }

    private String checkRequiredPermission(String key) {
        // TODO change to configurable map
        switch (key) {
            case VSS.PROPERTY_GROUP_A_PROP1:
                return VSS.PERMISSION_VSS_GROUP_A;
            case VSS.PROPERTY_GROUP_B_PROP2:
                return VSS.PERMISSION_VSS_GROUP_B;
        }
        throw new RuntimeException("Unknown Property " + key);
    }
}

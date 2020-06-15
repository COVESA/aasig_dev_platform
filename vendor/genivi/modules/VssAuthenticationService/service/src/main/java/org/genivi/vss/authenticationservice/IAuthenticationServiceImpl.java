// Copyright (C) 2020 TietoEVRY
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

package org.genivi.vss.authenticationservice;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Binder;
import android.os.RemoteException;
import android.util.Log;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class IAuthenticationServiceImpl extends IAuthenticationService.Stub {
    private final static String TAG = IAuthenticationServiceImpl.class.getSimpleName();
    private final Context mContext;

    IAuthenticationServiceImpl(Context context) {
        mContext = context;
    }

    @Override
    public String getAuthenticationToken() throws RemoteException {
        try {
            List<String> grantedPermissions = getGrantedPermissions();
            Log.d(TAG, "Permissions: "Arrays.toString(new List[]{grantedPermissions}));
        } catch (PackageManager.NameNotFoundException e) {
            e.printStackTrace();
        }
        // TODO Generate JWT with fetched permisions
        return null;
    }

    private List<String> getGrantedPermissions() throws PackageManager.NameNotFoundException {
        PackageManager packageManager = mContext.getPackageManager();
        PackageInfo packageInfo = packageManager.getPackageInfo(packageManager.getNameForUid(
                Binder.getCallingUid()), PackageManager.GET_PERMISSIONS);

        List<String> permissionList = new ArrayList<>();
        // requestedPermissions array contains both granted and non-granted permissions
        // using corresponding requestedPermissionsFlags array, filter out the non-granted ones
        for (int i = 0; i < packageInfo.requestedPermissions.length; i++) {
            if ((packageInfo.requestedPermissionsFlags[i] & PackageInfo.REQUESTED_PERMISSION_GRANTED) == PackageInfo.REQUESTED_PERMISSION_GRANTED) {
                permissionList.add(packageInfo.requestedPermissions[i]);
            }
        }
        return permissionList;
    }
}

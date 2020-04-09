// Copyright (C) 2020 TietoEVRY
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

// IAuthenticationService.aidl
package org.genivi.vss.authenticationservice;


interface IAuthenticationService {
    /**
     * Retrieves the token with bundled access information used by Vehicle Data Service
     */
    String getAuthenticationToken();
}

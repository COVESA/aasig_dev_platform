// IAuthenticationService.aidl
package org.genivi.vss.authenticationservice;


interface IAuthenticationService {
    /**
     * Retrieves the token with bundled access information used by Vehicle Data Service
     */
    String getAuthenticationToken();
}

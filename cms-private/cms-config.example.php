<?php
/**
 * ============================================================================================
 *  TOP 10 IRISH CASINO – PRIVATE CMS SETTINGS  (GitHub account + CMS logins)
 * ============================================================================================
 *
 *  1. Copy this file and name the copy  cms-config.php
 *  2. Put it on your web server OUTSIDE the public website folder, in a folder named cms-private:
 *
 *        /home/<your-cpanel-user>/cms-private/cms-config.php      <- here
 *        /home/<your-cpanel-user>/public_html/                     <- the website (index.html, admin/ …)
 *
 *     (It also works directly in public_html/cms-config.php – the website's .htaccess file
 *      blocks it from being opened or downloaded.)
 *
 *  3. Fill in the values below and save.
 *
 *  NEVER commit cms-config.php to GitHub or share it: it contains your GitHub access token.
 *  (.gitignore already keeps it out of the repository.)
 * ============================================================================================
 */

return [

    // ----------------------------------------------------------------------------------------
    // GitHub account / repository where the CMS saves all website content
    // ----------------------------------------------------------------------------------------
    'github' => [
        // The repository, as "owner/repository-name"
        'repo'   => 'rachelfenechdeltaservices-sys/ire-new',

        // The branch the live website is built from
        'branch' => 'adding-cms',

        // The folder in the repository that holds the website (content/, admin/, index.html …).
        // Use '' (empty) if those files are at the top level of the repository.
        'root_dir' => 'updated-website',

        // A GitHub fine-grained personal access token for the account above:
        //   GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
        //   → Generate new token
        //     • Repository access: Only select repositories → this repository
        //     • Permissions → Repository permissions → Contents: Read and write
        //       (Metadata: Read-only is added automatically)
        //     • Expiration: up to 1 year – set a reminder to renew it
        'token'  => 'github_pat_PASTE_YOUR_TOKEN_HERE',
    ],

    // ----------------------------------------------------------------------------------------
    // People who can sign in to the CMS at https://top10irishcasino.site/admin/
    //   'username' => 'password hash',
    // Create each line at https://top10irishcasino.site/admin/make-password.php
    // (passwords are stored as one-way hashes, never as plain text)
    // ----------------------------------------------------------------------------------------
    'users' => [
        // 'rachel' => '$2y$10$...........................................',
    ],

    // ----------------------------------------------------------------------------------------
    // Sign-in protection: after this many wrong passwords from one IP address,
    // that address has to wait before trying again.
    // ----------------------------------------------------------------------------------------
    'max_attempts'    => 5,
    'lockout_minutes' => 15,
];

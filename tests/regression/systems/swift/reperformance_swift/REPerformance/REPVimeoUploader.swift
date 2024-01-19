//
//  REPVimeoUploader.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-06-12.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import VimeoNetworking
import VimeoUpload

class REPVimeoUploader: VimeoUploader<OldUploadDescriptor>
{
    init(backgroundSessionIdentifier: String, accessTokenProvider: @escaping VimeoRequestSerializer.AccessTokenProvider) {
		super.init(backgroundSessionIdentifier: backgroundSessionIdentifier, accessTokenProvider: accessTokenProvider, apiVersion: "3.3.1")!
    }
}

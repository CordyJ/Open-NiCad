//
//  REPVimeoUploaderManager.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-06-15.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import VimeoNetworking
import VimeoUpload
import Photos


class REPVimeoUploaderManager: NSObject {
	
	static let sharedVideoManager = REPVimeoUploaderManager()
	var videoUploader: REPVimeoUploader?
	var uploadIdentifier: String?
	var uploadCompletion: ((String?, Error?)->())?
	var timeoutTimer: Timer?
	
	
	override init() {
		super.init()
		
		NotificationCenter.default.addObserver(self, selector: #selector(REPVimeoUploaderManager.uploadSucceededNotificationHandler(notification:)), name: Notification.Name(DescriptorManagerNotification.DescriptorDidSucceed.rawValue), object: nil)
		NotificationCenter.default.addObserver(self, selector: #selector(REPVimeoUploaderManager.uploadFailedNotificationHandler(notification:)), name: Notification.Name(DescriptorManagerNotification.DescriptorDidFail.rawValue), object: nil)
		NotificationCenter.default.addObserver(self, selector: #selector(REPVimeoUploaderManager.uploadInvalidatedNotificationHandler(notification:)), name: Notification.Name(DescriptorManagerNotification.SessionDidBecomeInvalid.rawValue), object: nil)
		
		videoUploader = REPVimeoUploader(backgroundSessionIdentifier: Constants.Vimeo.BackgroundIdentifier) { () -> String? in
			return Constants.Vimeo.AuthKey
		}
	}
	
	
	@objc
	func uploadSucceededNotificationHandler(notification: NSNotification) {
		if let descriptor = notification.object as? OldUploadDescriptor,
			let descriptorIdentifier = descriptor.identifier, let videoUri = descriptor.videoUri, descriptorIdentifier == self.uploadIdentifier {
			DispatchQueue.main.async {
				if let uploadCompletion = self.uploadCompletion {
					let vimeoID = videoUri.replacingOccurrences(of: "/videos/", with: "") // strip out "/videos/" from "/videos/******/"
					uploadCompletion(vimeoID, nil)
					self.uploadCompletion = nil
					self.timeoutTimer?.invalidate()
				}
			}
		}
	}
	
	@objc
	func uploadFailedNotificationHandler(notification: NSNotification) {
		if let descriptor = notification.object as? OldUploadDescriptor, let error = descriptor.error {
			DispatchQueue.main.async {
				if let uploadCompletion = self.uploadCompletion {
					uploadCompletion(nil, error)
					self.uploadCompletion = nil
					self.timeoutTimer?.invalidate()
				}
			}
		}
	}
	
	@objc
	func uploadInvalidatedNotificationHandler(notification: NSNotification) {
		if let descriptor = notification.object as? OldUploadDescriptor {
			if uploadCompletion != nil {
				REPVimeoUploaderManager.sharedVideoManager.videoUploader?.uploadVideo(descriptor: descriptor)
			}
		}
	}
	
	@objc
	func uploadTimeoutHandler() {
		DispatchQueue.main.async {
			if let uploadCompletion = self.uploadCompletion, let identifier = self.uploadIdentifier {
				REPVimeoUploaderManager.sharedVideoManager.videoUploader?.cancelUpload(identifier: identifier)
				uploadCompletion(nil, NSError(domain: "Vimeo.Timeout", code: 400, userInfo: nil))
				self.uploadCompletion = nil
			}
		}
		
		self.timeoutTimer?.invalidate()
	}
}


extension REPVimeoUploaderManager {
	
	func uploadToVimeo(asset: AVURLAsset, identifier: String, completionBlock: @escaping (String?, Error?)->()) {
		let exportOperation = ExportOperation(asset: asset)
		exportOperation.completionBlock = {
			guard exportOperation.isCancelled == false else {
				return
			}
			
			if let error = exportOperation.error {
				completionBlock(nil, error)
			} else if let url = exportOperation.outputURL {
				let descriptor = OldUploadDescriptor(url: url)
				descriptor.identifier = identifier
				
				self.uploadIdentifier = identifier
				self.uploadCompletion = completionBlock
				
				// Dispatch a Time out timer to avoid no network timeout
				DispatchQueue.main.async {
					self.timeoutTimer = Timer.scheduledTimer(timeInterval: Constants.Vimeo.UploadTimeout, target: self, selector: #selector(REPVimeoUploaderManager.uploadTimeoutHandler), userInfo: nil, repeats: false)
				}
				
				REPVimeoUploaderManager.sharedVideoManager.videoUploader?.uploadVideo(descriptor: descriptor)
				
			} else {
				assertionFailure("error and outputURL are mutually exclusive, this should never happen.")
			}
		}
		exportOperation.start()
	}
}

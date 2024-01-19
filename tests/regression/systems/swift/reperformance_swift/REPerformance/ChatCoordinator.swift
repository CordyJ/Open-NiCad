//
//  ChatCoordinator.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit
import Result
import Moya
import FirebaseAuth
import FirebaseFirestore
import FirebaseFunctions
import NVActivityIndicatorView


class ChatCoordinator: NSObject {
	
	let chatServiceProvider = MoyaProvider<ChatService>()
	let navigationController: UINavigationController = UINavigationController()
	
	static var UnreadMessagesCount: Int = 0
	
	lazy var functions = Functions.functions()
	
	
	func start(presenting viewController: UIViewController, athlete: Athlete? = nil) {
		NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		self.signIn() { (signInResult) in
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
			
			guard case .success(_) = signInResult else {
				return
			}
			
			guard let personalFirebaseUserIdentifier = Auth.auth().currentUser?.uid else {
				return
			}
			
			let startingViewController: UIViewController
			if let athlete = athlete, "\(athlete.userIdentifier)" != UserDefaults.standard.userID {
				startingViewController = self.chatMessagesVC(personalFirebaseUserIdentifier: personalFirebaseUserIdentifier, athleteIdentifier: "\(athlete.userIdentifier)")
				startingViewController.navigationItem.title = athlete.name
			}
			else {
				startingViewController = self.chatUserListVC(personalFirebaseUserIdentifier: personalFirebaseUserIdentifier)
			}
			
			startingViewController.navigationItem.leftBarButtonItem = BlockBarButtonItem(barButtonSystemItem: .done) {
				viewController.dismiss(animated: true)
			}
			
			self.navigationController.viewControllers = [startingViewController]
			self.navigationController.delegate = self
			self.navigationController.navigationBar.barTintColor = ColorName.rePerformanceBlue.color
			self.navigationController.navigationBar.isTranslucent = false
			
			viewController.present(self.navigationController, animated: true)
		}
	}
	
	func start(presenting viewController: UIViewController, conversationIdentifier: String, name: String) {
		NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		self.signIn() { (signInResult) in
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
			
			guard case .success(_) = signInResult else {
				return
			}
			
			guard let personalFirebaseUserIdentifier = Auth.auth().currentUser?.uid else {
				return
			}
			
			let startingViewController = self.chatMessagesVC(personalFirebaseUserIdentifier: personalFirebaseUserIdentifier, conversationIdentifier: conversationIdentifier)
			startingViewController.navigationItem.title = name
			startingViewController.navigationItem.leftBarButtonItem = BlockBarButtonItem(barButtonSystemItem: .done) {
				viewController.dismiss(animated: true)
			}
			
			self.navigationController.viewControllers = [startingViewController]
			self.navigationController.delegate = self
			self.navigationController.navigationBar.barTintColor = ColorName.rePerformanceBlue.color
			self.navigationController.navigationBar.isTranslucent = false
			
			viewController.present(self.navigationController, animated: true)
		}
	}
	
	
	fileprivate func chatUserListVC(personalFirebaseUserIdentifier: String) -> ChatUserListViewController {
		let chatUserListViewController = StoryboardScene.Chat.chatUserListViewController.instantiate()
		chatUserListViewController.navigationItem.title = L10n.chatUsersTitle
		chatUserListViewController.selectedConversation = { (conversation) in
			guard let otherParticipantIdentifier = conversation.otherParticipantIdentifier else {
				return
			}
			
			let chatMessagesViewController = self.chatMessagesVC(personalFirebaseUserIdentifier: personalFirebaseUserIdentifier, athleteIdentifier: otherParticipantIdentifier)
            if let myProfileURL = conversation.me?.profileURL {
                if let image = UIImage.getSavedProfileImage() {
                    chatMessagesViewController.myProfileImage = image
                }
                else {
                    UIImage.userProfileImage(url: URL(string:myProfileURL), completion: { (image) in
                        chatMessagesViewController.myProfileImage = image
                    })
                }
            }
            if let otherProfileURL = conversation.otherParticipant?.profileURL {
                UIImage.userProfileImage(url: URL(string:otherProfileURL), completion: { (image) in
                    chatMessagesViewController.otherProfileImage = image
                })
            }
			chatMessagesViewController.navigationItem.title = conversation.otherParticipant?.fullName
			self.navigationController.pushViewController(chatMessagesViewController, animated: true)
		}
		chatUserListViewController.firebaseIdentifier = personalFirebaseUserIdentifier
		
		return chatUserListViewController
	}
	
	fileprivate func chatMessagesVC(personalFirebaseUserIdentifier: String, athleteIdentifier: String) -> ChatMessagesViewController {
		let chatMessagesViewController = StoryboardScene.Chat.chatMessagesViewController.instantiate()
		
		let startConversation = { (conversationIdentifier: String) in
			chatMessagesViewController.messagingIdentifiers = (personalFirebaseUserIdentifier, conversationIdentifier)
		}
		
		self.lookupConversationIdentifier(for: athleteIdentifier) { (lookupConversationIdentifierResult) in
			if case .success(let identifier) = lookupConversationIdentifierResult {
				if let identifier = identifier {
					startConversation(identifier)
				}
				else {
					self.createConversation(for: athleteIdentifier) { (createConversationResult) in
						if case .success(let identifier) = createConversationResult {
							startConversation(identifier)
						}
					}
				}
			}
		}
		
		return chatMessagesViewController
	}
	
	fileprivate func chatMessagesVC(personalFirebaseUserIdentifier: String, conversationIdentifier: String) -> ChatMessagesViewController {
		let chatMessagesViewController = StoryboardScene.Chat.chatMessagesViewController.instantiate()
		chatMessagesViewController.messagingIdentifiers = (personalFirebaseUserIdentifier, conversationIdentifier)
		
		return chatMessagesViewController
	}
	
	func signIn(completion: @escaping (Result<String, REPerformanceError>)->()) {
		self.fetchAuthToken() { (fetchAuthTokenResult) in
			switch fetchAuthTokenResult {
			case .success(let authToken):
				self.signIntoFirebase(token: authToken) { (signIntoFirebaseError) in
					if let error = signIntoFirebaseError {
						completion(.failure(error))
					}
					else {
						completion(.success(authToken))
					}
				}
			case .failure(let error):
				completion(.failure(error))
			}
		}
	}
	
	fileprivate struct AuthTokenResponse: Decodable {
		
		private enum CodingKeys: String, CodingKey {
			case token = "token"
		}
		
		let token: String
		
		
		init(from decoder: Decoder) throws {
			let container = try decoder.container(keyedBy: CodingKeys.self)
			self.token = try container.decode(String.self, forKey: .token)
		}
	}
	
	fileprivate func fetchAuthToken(completion: @escaping (Result<String, REPerformanceError>)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(.failure(REPerformanceError.userTokenMissing))
			return
		}
		
		self.chatServiceProvider.request(.generateAuthToken(token: token)) { result in
			do {
				let response = try result.dematerialize()
				let authTokenResponse = try response.map(REPerformanceBaseResponse<AuthTokenResponse>.self)
				completion(.success(authTokenResponse.data.token))
			} catch {
				let errorMessage = error.localizedDescription
				completion(.failure(REPerformanceError.requestFailed(errorMessage)))
			}
		}
	}
	
	fileprivate func signIntoFirebase(token: String, completion: @escaping (REPerformanceError?)->()) {
		Auth.auth().signIn(withCustomToken: token) { (firebaseSignInResult, error) in
			if let error = error {
				completion(.requestFailed(error.localizedDescription))
			}
			else {
				completion(nil)
			}
		}
	}
	
	fileprivate func lookupConversationIdentifier(for userIdentifier: String, completion: @escaping (Result<String?, REPerformanceError>)->()) {
		let param = ["userId" : userIdentifier]
		
		self.functions.httpsCallable("getConversation").call(param) { (result, error) in
			if let result = result {
				let conversationIdentifier = result.data as? String
				completion(.success(conversationIdentifier))
			}
			else if let error = error {
				completion(.failure(REPerformanceError.requestFailed(error.localizedDescription)))
			}
			else {
				completion(.failure(REPerformanceError.requestFailed("")))
			}
		}
	}
	
	fileprivate func createConversation(for userIdentifier: String, completion: @escaping (Result<String, REPerformanceError>)->()) {
		let param = ["userId" : userIdentifier]
		
		self.functions.httpsCallable("createConversation").call(param) { (result, error) in
			if let conversationIdentifier = result?.data as? String {
				completion(.success(conversationIdentifier))
			}
			else if let error = error {
				completion(.failure(REPerformanceError.requestFailed(error.localizedDescription)))
			}
			else {
				completion(.failure(REPerformanceError.requestFailed("")))
			}
		}
	}
	
	
	class func getUnreadMessageCount(completion: @escaping (Result<Int, REPerformanceError>)->()) {
		let functions = Functions.functions()
		
		functions.httpsCallable("getUnreadCount").call(nil) { (result, error) in
			if let unreadCount = result?.data as? Int {
				ChatCoordinator.UnreadMessagesCount = unreadCount
				
				completion(.success(unreadCount))
			}
			else if let error = error {
				completion(.failure(REPerformanceError.requestFailed(error.localizedDescription)))
			}
			else {
				completion(.failure(REPerformanceError.requestFailed("")))
			}
		}
	}
}


extension ChatCoordinator: UINavigationControllerDelegate {
	
}

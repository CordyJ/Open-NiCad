//
//  ChatMessagesViewController.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit
import FirebaseFirestore
import FirebaseFunctions


class ChatMessagesViewController: UIViewController {
	
	@IBOutlet
	fileprivate var messagesTableView: UITableView?
	
	@IBOutlet
	fileprivate var messageTextField: UITextField?
    
    var myProfileImage: UIImage? = nil
    var otherProfileImage: UIImage? = nil
	
	
	@IBAction
	private func tappedSendButton(_ sender: Any?) {
		guard let messageToSend = self.messageTextField?.text, messageToSend.isEmpty == false else {
			return
		}
		
		guard let conversationIdentifier = self.messagingIdentifiers?.conversationIdentifier else {
			return
		}
		
		self.sendMessage(converstationIdentifier: conversationIdentifier, message: messageToSend)
		
		self.messageTextField?.text = nil
		self.messageTextField?.resignFirstResponder()
	}
	
	
	deinit {
		self.snapshotListener?.remove()
        self.conversationSnapshotListener?.remove()
	}
	
	
	fileprivate let functions = Functions.functions()
	
	
	var messagingIdentifiers: (firebaseIdentifier: String, conversationIdentifier: String)? = nil {
		didSet {
			self.snapshotListener?.remove()
			
			guard let messagingIdentifiers = self.messagingIdentifiers else {
				return
			}

            // profile images update
            let conversationReference = Firestore.firestore().collection("conversations").document(messagingIdentifiers.conversationIdentifier)
            self.conversationSnapshotListener = conversationReference.addSnapshotListener { [weak self] (snapshot, error) in
                guard let snapshot = snapshot else {
                    return
                }
                
                let chatConversation = ChatConversation(snapshot: snapshot)
                if let myProfileURL = chatConversation.me?.profileURL {
                    if let image = UIImage.getSavedProfileImage() {
                        self?.myProfileImage = image
                    }
                    else {
                        UIImage.userProfileImage(url: URL(string:myProfileURL), completion: { (image) in
                            guard let image = image else { return }
                            self?.myProfileImage = image
                        })
                    }
                }
                if let otherProfileURL = chatConversation.otherParticipant?.profileURL {
                    UIImage.userProfileImage(url: URL(string:otherProfileURL), completion: { (image) in
                        guard let image = image else { return }
                        self?.otherProfileImage = image
                    })
                }
            }

            
			let conversationMessagesReference = Firestore.firestore().collection("conversations").document(messagingIdentifiers.conversationIdentifier).collection("messages").whereField(FieldPath(["user_ids"]), arrayContains: messagingIdentifiers.firebaseIdentifier)

			self.snapshotListener = conversationMessagesReference.addSnapshotListener() { [weak self] (snapshot, error) in
				guard let snapshot = snapshot else {
					return
				}
				
				var messages = [ChatMessage]()
				for document in snapshot.documents {
					let message = ChatMessage(snapshot: document)
					messages.append(message)
				}
				
				self?.messages = messages.sorted(by: { $0.date < $1.date })
				
				self?.markMessagesRead(for: messagingIdentifiers.conversationIdentifier)
			}
		}
	}
	
	fileprivate var snapshotListener: ListenerRegistration?
    fileprivate var conversationSnapshotListener: ListenerRegistration?

	fileprivate var messages: [ChatMessage]? = nil {
		didSet {
			self.messagesTableView?.reloadData()
			self.messagesTableView?.scrollToBottom()
		}
	}
	
	
	fileprivate func sendMessage(converstationIdentifier: String, message: String, completion: ((REPerformanceError?)->())? = nil) {
		let param = ["conversation_id" : converstationIdentifier, "text" : message]
		
		self.functions.httpsCallable("sendMessage").call(param) { (_, error) in
			if let error = error {
				completion?(REPerformanceError.requestFailed(error.localizedDescription))
			}
			else {
				completion?(nil)
			}
		}
	}
	
	fileprivate func markMessagesRead(for conversationIdentifier: String, completion: ((REPerformanceError?)->())? = nil) {
		let param = ["conversation_id" : conversationIdentifier]
		
		self.functions.httpsCallable("markMessagesAsRead").call(param) { (result, error) in
			if let error = error {
				completion?(REPerformanceError.requestFailed(error.localizedDescription))
			}
			else {
				(UIApplication.shared.delegate as? AppDelegate)?.appCoordinator?.mainCoordinator.reportCardCoordinator.refreshChatUnreadMessagesStatus()
				
				completion?(nil)
			}
		}
	}
}


extension ChatMessagesViewController: UITableViewDataSource {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		return 1
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		guard let messages = self.messages else {
			return 0
		}
		
		return messages.count
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		let message = self.messages![indexPath.row]
		let cellIdentifier = message.isOwner! ? "Chat Message Sent Cell Identifier" : "Chat Message Received Cell Identifier"
		let cell = tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! ChatMessageTableViewCell
		cell.messageContent = message.text
        if message.isOwner! {
            cell.messageImage.image = self.myProfileImage ?? Asset.Assets.nonFacebook.image
        }
        else {
            cell.messageImage.image = self.otherProfileImage ?? Asset.Assets.nonFacebook.image
        }
		
		return cell
	}
}


extension ChatMessagesViewController: UITextFieldDelegate {
	
	func textFieldShouldEndEditing(_ textField: UITextField) -> Bool {
		textField.resignFirstResponder()
		
		return true
	}
}

//
//  UIImage+REPerformance.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AlamofireImage

extension UIImage {
    class func oneByOneImage(with color: UIColor) -> UIImage? {
        let rect = CGRect(origin: CGPoint(x: 0, y:0), size: CGSize(width: 1, height: 1))
        UIGraphicsBeginImageContext(rect.size)
        
        var image:UIImage? = nil
        if let context = UIGraphicsGetCurrentContext() {
            context.setFillColor(color.cgColor)
            context.fill(rect)
            image = UIGraphicsGetImageFromCurrentImageContext()
        }
        UIGraphicsEndImageContext()
        return image
    }
    
    class func userProfileImage(url: URL?, completion: @escaping ((UIImage?)->())) {
        guard let profileURL = url else {
            completion(nil)
            return
        }
        let request = URLRequest(url: profileURL)
        ImageDownloader.default.download(request) { response in
            if let image = response.value {
                completion(image)
                return
            }
        }
        completion(nil)
    }
    
    class func getSavedProfileImage() -> UIImage? {
        if let dir = try? FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false) {
            return UIImage(contentsOfFile: URL(fileURLWithPath: dir.absoluteString).appendingPathComponent("userProfile.jpg").path)
        }
        return nil
    }
    
    class func saveProfileImage(image: UIImage) -> Bool {
        guard let data = image.jpegData(compressionQuality: 1.0) else {
            return false
        }
        guard let directory = try? FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false) as NSURL else {
            return false
        }
        do {
            try data.write(to: directory.appendingPathComponent("userProfile.jpg")!)
            return true
        } catch {
            print(error.localizedDescription)
            return false
        }
    }
}

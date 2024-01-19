//
//  CacheSubmissionManager.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-11-15.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class CacheSubmission: NSObject, NSCoding {
    
    let submissionID: Int
    let videoURL: URL
    let videoIdentifier: String
    
    init(videoURL: URL, submissionID: Int, videoIdentifier: String) {
        self.videoURL = videoURL
        self.submissionID = submissionID
        self.videoIdentifier = videoIdentifier
    }
    
    required init?(coder aDecoder: NSCoder) {
        guard let videoURL = aDecoder.decodeObject(forKey: "videoURL") as? URL else { return nil }
        guard let videoIdentifier = aDecoder.decodeObject(forKey: "videoIdentifier") as? String else { return nil }

        self.submissionID = aDecoder.decodeInteger(forKey: "submissionID")

        self.videoURL = videoURL
        self.videoIdentifier = videoIdentifier
        
        super.init()
    }
    
    func encode(with aCoder: NSCoder) {
        aCoder.encode(self.submissionID, forKey: "submissionID")
        aCoder.encode(self.videoURL, forKey: "videoURL")
        aCoder.encode(self.videoIdentifier, forKey: "videoIdentifier")
    }
}


class CacheSubmissionManager: NSObject {

    var cacheSubmissions: [CacheSubmission] = {
        let directory = CacheSubmissionManager.cacheFile()
        let submissions = NSKeyedUnarchiver.unarchiveObject(withFile: directory.path) as? [CacheSubmission]
        return submissions ?? [CacheSubmission]()
    }()
    
    /// Returns the videoURL with the current sandbox path since the sandbox path can change.
    func videoURLInCurrentSandbox(url: URL) -> URL {
        return CacheSubmissionManager.applicationSupportDirectory().appendingPathComponent(url.lastPathComponent)
    }
    
    class func saveVideo(videoURL:URL?) -> URL? {
        guard let videoURL = videoURL else {
            return nil
        }
        
        do {
            let fm = FileManager.default
            let videoData = try NSData(contentsOf: videoURL, options: [.uncached])
            let applicationURL = CacheSubmissionManager.applicationSupportDirectory()
            let filename = DateFormatter.storedDateFormatter().string(from: Date())
            let videoDataURL = applicationURL.appendingPathComponent("\(filename).mov")
            print(videoDataURL)
            if (fm.fileExists(atPath: videoDataURL.path)) {
                try fm.removeItem(at: videoDataURL)
            }
            try videoData.write(to: videoDataURL, options: .atomic)
            return videoDataURL
        }
        catch let error {
            print("Error saving video: \(error)")
            return nil
        }
    }
    
    //This gets called every time the user leaves the exercisesSubmissionResultsViewController to go to leaderboard or clicks done button. If they leave without doing either of those two things the videos will continue to exist in the tmp folder. iOS will eventually purge this folder next time the device is restarted.
    class func deleteVideo(videoURL:URL?) {
        guard let videoURL = videoURL else {
            return
        }
        let fileManager = FileManager.default
        if(fileManager.fileExists(atPath: videoURL.path)){
            do{
                try fileManager.removeItem(atPath: videoURL.path)
            } catch let error as NSError {
                print(error.debugDescription)
                return
            }
        }
    }

    
    fileprivate class func applicationSupportDirectory() -> URL {
        do {
            let bundleID = Bundle.main.bundleIdentifier ?? "push_interactions"
            let fm = FileManager.default
            let applicationSupportUrl = try fm.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
            let bundleURL = applicationSupportUrl.appendingPathComponent(bundleID)
            
            if !(fm.fileExists(atPath: bundleURL.path)) {
                try fm.createDirectory(at: bundleURL, withIntermediateDirectories: false, attributes: nil)
            }
            return bundleURL
        }
        catch let error as NSError {
            fatalError("Error creating directory: \(error.localizedDescription)")
        }
    }
    
    fileprivate class func cacheFile() -> URL {
        let directory = CacheSubmissionManager.applicationSupportDirectory()
        return directory.appendingPathComponent("cacheSubmissions.data")
    }

    func saveSubmissions(saveSubmission:CacheSubmission) {
        var cacheSubmissions = self.cacheSubmissions
        
        // check if the cacheSubmission has already been saved.
        for submission in cacheSubmissions {
            if submission.submissionID == saveSubmission.submissionID {
                return
            }
        }
        cacheSubmissions.append(saveSubmission)
        let directory = CacheSubmissionManager.cacheFile()
        let saved = NSKeyedArchiver.archiveRootObject(cacheSubmissions, toFile: directory.path)
        print(saved)
    }
    
    func removeSubmission(submission:CacheSubmission) {
        var cacheSubmissions = self.cacheSubmissions
        
        if let index = cacheSubmissions.index(of: submission) {
            let videoURL = videoURLInCurrentSandbox(url: submission.videoURL)
            CacheSubmissionManager.deleteVideo(videoURL: videoURL)
            cacheSubmissions.remove(at: index)
            let directory = CacheSubmissionManager.cacheFile()
            NSKeyedArchiver.archiveRootObject(cacheSubmissions, toFile: directory.path)
        }
    }
    
    func clearExpiredMovieFiles() {
        // Get the document directory url
        let fm = FileManager.default
        let applicationURL = CacheSubmissionManager.applicationSupportDirectory()

        do {
            // Get the directory contents urls (including subfolders urls)
            let directoryContents = try fm.contentsOfDirectory(at: applicationURL, includingPropertiesForKeys: nil, options: [])
            print(directoryContents)
            
            // if you want to filter the directory contents you can do like this:
            let movFiles = directoryContents.filter{ $0.pathExtension == "mov" }
        /* Can I please keep these commented code for debugging...  PLEASE PLEASE
            print("mov urls:",movFiles)
            let movFileNames = movFiles.map{ $0.deletingPathExtension().lastPathComponent }
            print("mov list:", movFileNames)
        */
 
            for movieFileURL in movFiles {
                // Since we are using the same directory, we can just compare the last component (filename.ext) which also avoids issues with changing sandbox paths.
                if let _ = cacheSubmissions.first(where: {
                    movieFileURL.lastPathComponent == $0.videoURL.lastPathComponent }) {
                    break
                }
                let movieFilename = movieFileURL.deletingPathExtension().lastPathComponent
                let filenameDate = DateFormatter.storedDateFormatter().date(from: movieFilename)
                if let filenameDate = filenameDate, filenameDate.timeIntervalSinceNow < -(Constants.Vimeo.VideoExpiration) {
                    try fm.removeItem(at: movieFileURL)
                }
            }
            
        } catch {
            print(error.localizedDescription)
        }
    }
}
